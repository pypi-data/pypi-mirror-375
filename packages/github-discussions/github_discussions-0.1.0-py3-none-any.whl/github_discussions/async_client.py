"""Async GitHub Discussions GraphQL client."""

import asyncio
from typing import Any, Dict, List, Optional, cast

import aiohttp

from .base_client import (
    BaseGitHubDiscussionsClient,
    Discussion,
    DiscussionCategory,
    DiscussionComment,
)
from .exceptions import (
    AuthenticationError,
    GitHubGraphQLError,
    NetworkError,
    NotFoundError,
    PermissionError,
    RateLimitError,
)


class AsyncGitHubDiscussionsClient(BaseGitHubDiscussionsClient):
    """Async client for interacting with GitHub Discussions via GraphQL API."""

    def __init__(
        self,
        token: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
        base_url: Optional[str] = None,
        connector: Optional[aiohttp.BaseConnector] = None,
    ):
        """Initialize the async GitHub Discussions GraphQL client.

        Args:
            token: GitHub personal access token or installation token
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff: Backoff multiplier for retries
            base_url: Custom GraphQL API base URL (for GitHub Enterprise)
            connector: Custom aiohttp connector
        """
        super().__init__(token, timeout, max_retries, retry_backoff, base_url)
        self.connector = connector

        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "GitHub-Discussions-GraphQL-Async/0.1.0",
        }

    def _make_request(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make an async GraphQL request to GitHub API.

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

        async def _async_request() -> Dict[str, Any]:
            for attempt in range(self.max_retries + 1):
                try:
                    async with aiohttp.ClientSession(
                        connector=self.connector, headers=self._headers
                    ) as session:
                        async with session.post(
                            self.base_url,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=self.timeout),
                        ) as response:
                            # Handle rate limiting
                            if response.status == 403:
                                reset_time = response.headers.get("X-RateLimit-Reset")
                                if reset_time:
                                    reset_at = (
                                        asyncio.get_event_loop().time()
                                        + int(reset_time)
                                        - asyncio.get_event_loop().time()
                                    )
                                    raise RateLimitError(
                                        "Rate limit exceeded",
                                        reset_at=str(reset_at),
                                        limit=int(
                                            response.headers.get("X-RateLimit-Limit", 0)
                                        ),
                                        remaining=int(
                                            response.headers.get(
                                                "X-RateLimit-Remaining", 0
                                            )
                                        ),
                                        status_code=response.status,
                                    )

                            # Handle authentication errors
                            if response.status == 401:
                                raise AuthenticationError(
                                    "Authentication failed",
                                    status_code=response.status,
                                )

                            # Handle not found errors
                            if response.status == 404:
                                raise NotFoundError(
                                    "Resource not found",
                                    status_code=response.status,
                                )

                            # Handle permission errors
                            if response.status == 403:
                                raise PermissionError(
                                    "Insufficient permissions",
                                    status_code=response.status,
                                )

                            response.raise_for_status()

                            data = cast(Dict[str, Any], await response.json())

                            # Handle GraphQL errors
                            if "errors" in data:
                                self._handle_graphql_errors(data["errors"])

                            return data

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt == self.max_retries:
                        raise NetworkError(f"Network error: {str(e)}")
                    await asyncio.sleep(self.retry_backoff**attempt)

            raise GitHubGraphQLError("Max retries exceeded")

        return asyncio.run(_async_request())

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

    async def __aenter__(
        self: "AsyncGitHubDiscussionsClient",
    ) -> "AsyncGitHubDiscussionsClient":
        return self

    async def __aexit__(
        self: "AsyncGitHubDiscussionsClient", exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        pass
