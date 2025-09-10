"""Synchronous GitHub Discussions GraphQL client."""

import time
from typing import Any, Dict, Iterator, List, Optional, cast

import requests

from .base_client import (
    BaseGitHubDiscussionsClient,
    Discussion,
    DiscussionCategory,
    DiscussionComment,
    DiscussionsResponse,
    RateLimitStatus,
)
from .exceptions import (
    AuthenticationError,
    GitHubGraphQLError,
    NetworkError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    TimeoutError,
)


class GitHubDiscussionsClient(BaseGitHubDiscussionsClient):
    """Synchronous client for interacting with GitHub Discussions via GraphQL API."""

    def __init__(
        self,
        token: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
        base_url: Optional[str] = None,
    ):
        """Initialize the GitHub Discussions GraphQL client.

        Args:
            token: GitHub personal access token or installation token
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff: Backoff multiplier for retries
            base_url: Custom GraphQL API base URL (for GitHub Enterprise)
        """
        super().__init__(token, timeout, max_retries, retry_backoff, base_url)

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "GitHub-Discussions-GraphQL/0.1.0",
            }
        )

    def _make_request(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make a synchronous GraphQL request to GitHub API.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name for the query

        Returns:
            Response data from GitHub API
        """
        payload: Dict[str, Any] = {"query": query}
        if variables is not None:
            payload["variables"] = variables
        if operation_name is not None:
            payload["operationName"] = operation_name

        for attempt in range(self.max_retries + 1):
            try:
                response = self._session.post(
                    self.base_url,
                    json=payload,
                    timeout=self.timeout,
                )

                # Handle rate limiting
                if response.status_code == 403:
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    if reset_time:
                        reset_at = time.strftime(
                            "%Y-%m-%d %H:%M:%S UTC", time.gmtime(int(reset_time))
                        )
                        raise RateLimitError(
                            "Rate limit exceeded",
                            reset_at=reset_at,
                            limit=int(response.headers.get("X-RateLimit-Limit", 0)),
                            remaining=int(
                                response.headers.get("X-RateLimit-Remaining", 0)
                            ),
                            status_code=response.status_code,
                        )

                # Handle authentication errors
                if response.status_code == 401:
                    raise AuthenticationError(
                        "Authentication failed",
                        status_code=response.status_code,
                    )

                # Handle not found errors
                if response.status_code == 404:
                    raise NotFoundError(
                        "Resource not found",
                        status_code=response.status_code,
                    )

                # Handle permission errors
                if response.status_code == 403:
                    raise PermissionError(
                        "Insufficient permissions",
                        status_code=response.status_code,
                    )

                response.raise_for_status()

                data = cast(Dict[str, Any], response.json())

                # Handle GraphQL errors
                if "errors" in data:
                    self._handle_graphql_errors(data["errors"])

                return data

            except requests.exceptions.Timeout:
                if attempt == self.max_retries:
                    raise TimeoutError("Request timed out")
                time.sleep(self.retry_backoff**attempt)

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    raise NetworkError(f"Network error: {str(e)}")
                time.sleep(self.retry_backoff**attempt)

        raise GitHubGraphQLError("Max retries exceeded")

    def get_rate_limit_status(self) -> RateLimitStatus:
        """Get current rate limit status.

        Returns:
            RateLimitStatus object with current rate limit information
        """
        return super().get_rate_limit_status()

    def get_discussions(
        self,
        owner: str,
        repo: str,
        first: int = 10,
        after: Optional[str] = None,
        category_id: Optional[str] = None,
        answered: Optional[bool] = None,
        order_by: Optional[Dict[str, str]] = None,
    ) -> DiscussionsResponse:
        """Get discussions for a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            first: Number of discussions to fetch
            after: Cursor for pagination
            category_id: Filter by category ID
            answered: Filter by answered status
            order_by: Sort order (e.g., {"field": "UPDATED_AT", "direction": "DESC"})

        Returns:
            DiscussionsResponse with discussions and pagination info
        """
        return super().get_discussions(
            owner, repo, first, after, category_id, answered, order_by
        )

    def get_discussion(self, owner: str, repo: str, number: int) -> Discussion:
        """Get a specific discussion by number.

        Args:
            owner: Repository owner
            repo: Repository name
            number: Discussion number

        Returns:
            Discussion object
        """
        return super().get_discussion(owner, repo, number)

    def create_discussion(
        self,
        repository_id: str,
        category_id: str,
        title: str,
        body: str,
        client_mutation_id: Optional[str] = None,
    ) -> Discussion:
        """Create a new discussion.

        Args:
            repository_id: ID of the repository
            category_id: ID of the discussion category
            title: Discussion title
            body: Discussion body content
            client_mutation_id: Optional client mutation ID

        Returns:
            Created Discussion object
        """
        return super().create_discussion(
            repository_id, category_id, title, body, client_mutation_id
        )

    def get_discussion_comments(
        self,
        discussion_id: str,
        first: int = 10,
        after: Optional[str] = None,
    ) -> List[DiscussionComment]:
        """Get comments for a discussion.

        Args:
            discussion_id: ID of the discussion
            first: Number of comments to fetch
            after: Cursor for pagination

        Returns:
            List of DiscussionComment objects
        """
        return super().get_discussion_comments(discussion_id, first, after)

    def add_discussion_comment(
        self,
        discussion_id: str,
        body: str,
        reply_to_id: Optional[str] = None,
        client_mutation_id: Optional[str] = None,
    ) -> DiscussionComment:
        """Add a comment to a discussion.

        Args:
            discussion_id: ID of the discussion
            body: Comment body content
            reply_to_id: ID of the comment to reply to (optional)
            client_mutation_id: Optional client mutation ID

        Returns:
            Created DiscussionComment object
        """
        return super().add_discussion_comment(
            discussion_id, body, reply_to_id, client_mutation_id
        )

    def get_discussion_categories(
        self,
        owner: str,
        repo: str,
        first: int = 25,
        after: Optional[str] = None,
    ) -> List[DiscussionCategory]:
        """Get discussion categories for a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            first: Number of categories to fetch
            after: Cursor for pagination

        Returns:
            List of DiscussionCategory objects
        """
        return super().get_discussion_categories(owner, repo, first, after)

    def get_pinned_discussions(
        self,
        owner: str,
        repo: str,
        first: int = 10,
        after: Optional[str] = None,
    ) -> List[Discussion]:
        """Get pinned discussions for a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            first: Number of pinned discussions to fetch
            after: Cursor for pagination

        Returns:
            List of pinned Discussion objects
        """
        return super().get_pinned_discussions(owner, repo, first, after)

    def get_discussions_paginated(
        self,
        owner: str,
        repo: str,
        first: int = 10,
        category_id: Optional[str] = None,
        answered: Optional[bool] = None,
        order_by: Optional[Dict[str, str]] = None,
    ) -> Iterator[List[Discussion]]:
        """Get discussions with automatic pagination.

        Args:
            owner: Repository owner
            repo: Repository name
            first: Number of discussions per page
            category_id: Filter by category ID
            answered: Filter by answered status
            order_by: Sort order

        Yields:
            Lists of Discussion objects for each page
        """
        cursor = None
        while True:
            response = super().get_discussions(
                owner, repo, first, cursor, category_id, answered, order_by
            )

            if not response.discussions:
                break

            yield response.discussions

            # Check if there are more pages
            if not response.pagination.has_next_page:
                break

            cursor = response.pagination.end_cursor

    def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a custom GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name

        Returns:
            Raw response data from GitHub API
        """
        return super().execute_query(query, variables, operation_name)

    def __enter__(self: "GitHubDiscussionsClient") -> "GitHubDiscussionsClient":
        return self

    def __exit__(
        self: "GitHubDiscussionsClient", exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        self._session.close()
