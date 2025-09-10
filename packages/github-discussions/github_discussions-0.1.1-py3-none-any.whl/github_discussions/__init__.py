"""GitHub Discussions GraphQL Client.

A comprehensive Python package for interacting with GitHub Discussions
using the GraphQL API.
"""

__version__ = "0.1.1"
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

# Optional xAI integration - only available if dependencies are installed
try:
    from .xai_chat_integration import GitHubDiscussionsAssistant
    from .xai_function_calling import setup_github_discussions_tools

    _XAI_AVAILABLE = True
except ImportError:
    _XAI_AVAILABLE = False
    setup_github_discussions_tools = None
    GitHubDiscussionsAssistant = None

# Build __all__ list conditionally
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

# Add xAI functionality to __all__ if available
if _XAI_AVAILABLE:
    __all__.extend(
        [
            "setup_github_discussions_tools",
            "GitHubDiscussionsAssistant",
        ]
    )
