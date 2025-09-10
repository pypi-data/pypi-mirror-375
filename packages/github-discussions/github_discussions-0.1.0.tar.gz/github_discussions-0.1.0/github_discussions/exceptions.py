"""Custom exceptions for GitHub Discussions GraphQL client."""

from typing import Any, Dict, Optional


class GitHubGraphQLError(Exception):
    """Base exception for GitHub GraphQL API errors."""

    def __init__(
        self,
        message: str,
        errors: Optional[list] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.errors = errors or []
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        if self.errors:
            error_messages = [error.get("message", "") for error in self.errors]
            return f"{self.message}: {'; '.join(error_messages)}"
        return self.message


class RateLimitError(GitHubGraphQLError):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        reset_at: Optional[str] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.reset_at = reset_at
        self.limit = limit
        self.remaining = remaining

    def __str__(self) -> str:
        reset_info = f" (resets at {self.reset_at})" if self.reset_at else ""
        return f"Rate limit exceeded{reset_info}: {self.message}"


class AuthenticationError(GitHubGraphQLError):
    """Exception raised when authentication fails."""

    pass


class ValidationError(GitHubGraphQLError):
    """Exception raised when request validation fails."""

    pass


class NotFoundError(GitHubGraphQLError):
    """Exception raised when requested resource is not found."""

    pass


class PermissionError(GitHubGraphQLError):
    """Exception raised when user lacks required permissions."""

    pass


class NetworkError(GitHubGraphQLError):
    """Exception raised when network request fails."""

    pass


class TimeoutError(GitHubGraphQLError):
    """Exception raised when request times out."""

    pass
