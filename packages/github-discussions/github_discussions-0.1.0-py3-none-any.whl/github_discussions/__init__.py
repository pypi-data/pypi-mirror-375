"""GitHub Discussions GraphQL Client.

A comprehensive Python package for interacting with GitHub Discussions
using the GraphQL API.
"""

__version__ = "0.1.0"
__author__ = "Bill Schumacher"
__email__ = "34168009+BillSchumacher@users.noreply.github.com"

from .async_client import AsyncGitHubDiscussionsClient
from .base_client import (
    Discussion,
    DiscussionAuthor,
    DiscussionCategory,
    DiscussionComment,
    DiscussionsResponse,
    PaginationInfo,
    RateLimitStatus,
)
from .client import GitHubDiscussionsClient
from .exceptions import (
    AuthenticationError,
    GitHubGraphQLError,
    NetworkError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)

__all__ = [
    "GitHubDiscussionsClient",
    "AsyncGitHubDiscussionsClient",
    "RateLimitStatus",
    "DiscussionAuthor",
    "DiscussionCategory",
    "DiscussionComment",
    "Discussion",
    "DiscussionsResponse",
    "PaginationInfo",
    "GitHubGraphQLError",
    "RateLimitError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "PermissionError",
    "NetworkError",
    "TimeoutError",
]
