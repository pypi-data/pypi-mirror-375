"""Base GitHub Discussions GraphQL client with shared functionality."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional

from pydantic import BaseModel

from .exceptions import (
    AuthenticationError,
    GitHubGraphQLError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ValidationError,
)


class PaginationInfo(BaseModel):
    """Pagination information for a connection."""

    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None


class RateLimitStatus(BaseModel):
    """Rate limit status information."""

    limit: int
    remaining: int
    used: int
    reset_at: str


class DiscussionAuthor(BaseModel):
    """Author information for a discussion."""

    login: str
    avatar_url: Optional[str] = None
    url: Optional[str] = None


class DiscussionCategory(BaseModel):
    """Discussion category information."""

    id: str
    name: str
    description: Optional[str] = None
    emoji: Optional[str] = None
    is_answerable: bool = False


class DiscussionComment(BaseModel):
    """Discussion comment information."""

    id: str
    body: str
    body_html: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    author: Optional[DiscussionAuthor] = None
    reply_to: Optional[str] = None
    is_answer: bool = False


class Discussion(BaseModel):
    """Discussion information."""

    id: str
    number: int
    title: str
    body: str
    body_html: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    author: Optional[DiscussionAuthor] = None
    category: Optional[DiscussionCategory] = None
    comments_count: int = 0
    is_answered: bool = False
    is_locked: bool = False
    is_pinned: bool = False
    url: Optional[str] = None


class DiscussionsResponse(BaseModel):
    """Response containing discussions and pagination info."""

    discussions: List[Discussion]
    pagination: PaginationInfo


class BaseGitHubDiscussionsClient(ABC):
    """Base class for GitHub Discussions GraphQL clients."""

    GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(
        self,
        token: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
        base_url: Optional[str] = None,
    ):
        """Initialize the base GitHub Discussions GraphQL client.

        Args:
            token: GitHub personal access token or installation token
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff: Backoff multiplier for retries
            base_url: Custom GraphQL API base URL (for GitHub Enterprise)
        """
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.base_url = base_url or self.GITHUB_GRAPHQL_URL

    @abstractmethod
    def _make_request(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make a GraphQL request to GitHub API.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name for the query

        Returns:
            Response data from GitHub API
        """
        pass

    def _handle_graphql_errors(self, errors: List[Dict[str, Any]]) -> None:
        """Handle GraphQL-specific errors.

        Args:
            errors: List of GraphQL errors

        Raises:
            GitHubGraphQLError: For various GraphQL error types
        """
        if not errors:
            return

        error_messages = []
        for error in errors:
            message = error.get("message", "Unknown error")

            if "rate limit" in message.lower():
                raise RateLimitError(message, errors=errors)
            elif (
                "authentication" in message.lower() or "credentials" in message.lower()
            ):
                raise AuthenticationError(message, errors=errors)
            elif "not found" in message.lower() or "does not exist" in message.lower():
                raise NotFoundError(message, errors=errors)
            elif "permission" in message.lower() or "access" in message.lower():
                raise PermissionError(message, errors=errors)
            elif "validation" in message.lower():
                raise ValidationError(message, errors=errors)

            error_messages.append(message)

        raise GitHubGraphQLError("; ".join(error_messages), errors=errors)

    def _parse_author(
        self, author_data: Optional[Dict[str, Any]]
    ) -> Optional[DiscussionAuthor]:
        """Parse author data from GraphQL response.

        Args:
            author_data: Author data from GraphQL response

        Returns:
            DiscussionAuthor object or None
        """
        if not author_data:
            return None

        return DiscussionAuthor(
            login=author_data["login"],
            avatar_url=author_data.get("avatarUrl"),
            url=author_data.get("url"),
        )

    def _parse_category(
        self, category_data: Optional[Dict[str, Any]]
    ) -> Optional[DiscussionCategory]:
        """Parse category data from GraphQL response.

        Args:
            category_data: Category data from GraphQL response

        Returns:
            DiscussionCategory object or None
        """
        if not category_data:
            return None

        return DiscussionCategory(
            id=category_data["id"],
            name=category_data["name"],
            description=category_data.get("description"),
            emoji=category_data.get("emoji"),
            is_answerable=category_data.get("isAnswerable", False),
        )

    def _parse_discussion(self, discussion_data: Dict[str, Any]) -> Discussion:
        """Parse discussion data from GraphQL response.

        Args:
            discussion_data: Discussion data from GraphQL response

        Returns:
            Discussion object
        """
        author = self._parse_author(discussion_data.get("author"))
        category = self._parse_category(discussion_data.get("category"))

        return Discussion(
            id=discussion_data["id"],
            number=discussion_data["number"],
            title=discussion_data["title"],
            body=discussion_data["body"],
            body_html=discussion_data.get("bodyHTML"),
            created_at=discussion_data["createdAt"],
            updated_at=discussion_data.get("updatedAt"),
            author=author,
            category=category,
            comments_count=discussion_data["comments"]["totalCount"],
            is_answered=discussion_data["isAnswered"],
            is_locked=discussion_data["isLocked"],
            is_pinned=discussion_data["isPinned"],
            url=discussion_data.get("url"),
        )

    def _parse_comment(self, comment_data: Dict[str, Any]) -> DiscussionComment:
        """Parse comment data from GraphQL response.

        Args:
            comment_data: Comment data from GraphQL response

        Returns:
            DiscussionComment object
        """
        author = self._parse_author(comment_data.get("author"))
        reply_to_data = comment_data.get("replyTo")
        reply_to = reply_to_data["id"] if reply_to_data else None

        return DiscussionComment(
            id=comment_data["id"],
            body=comment_data["body"],
            body_html=comment_data.get("bodyHTML"),
            created_at=comment_data["createdAt"],
            updated_at=comment_data.get("updatedAt"),
            author=author,
            reply_to=reply_to,
            is_answer=comment_data["isAnswer"],
        )

    def get_rate_limit_status(self) -> RateLimitStatus:
        """Get current rate limit status.

        Returns:
            RateLimitStatus object with current rate limit information
        """
        query = """
        query {
            rateLimit {
                limit
                remaining
                used
                resetAt
            }
        }
        """

        data = self._make_request(query)
        rate_limit_data = data["data"]["rateLimit"]

        return RateLimitStatus(
            limit=rate_limit_data["limit"],
            remaining=rate_limit_data["remaining"],
            used=rate_limit_data["used"],
            reset_at=rate_limit_data["resetAt"],
        )

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
        if order_by is None:
            order_by = {"field": "UPDATED_AT", "direction": "DESC"}

        query = """
        query($owner: String!, $repo: String!, $first: Int, $after: String,
              $categoryId: ID, $answered: Boolean, $orderBy: DiscussionOrder) {
            repository(owner: $owner, name: $repo) {
                discussions(first: $first, after: $after,
                           categoryId: $categoryId, answered: $answered,
                           orderBy: $orderBy) {
                    nodes {
                        id
                        number
                        title
                        body
                        bodyHTML
                        createdAt
                        updatedAt
                        author {
                            login
                            avatarUrl
                            url
                        }
                        category {
                            id
                            name
                            description
                            emoji
                            isAnswerable
                        }
                        comments {
                            totalCount
                        }
                        isAnswered
                        isLocked
                        isPinned
                        url
                    }
                    pageInfo {
                        hasNextPage
                        hasPreviousPage
                        startCursor
                        endCursor
                    }
                }
            }
        }
        """

        variables = {
            "owner": owner,
            "repo": repo,
            "first": first,
            "after": after,
            "categoryId": category_id,
            "answered": answered,
            "orderBy": order_by,
        }

        data = self._make_request(query, variables)
        discussions_data = data["data"]["repository"]["discussions"]
        page_info_data = discussions_data["pageInfo"]

        discussions = []
        for discussion_data in discussions_data["nodes"]:
            discussion = self._parse_discussion(discussion_data)
            discussions.append(discussion)

        pagination = PaginationInfo(
            has_next_page=page_info_data["hasNextPage"],
            has_previous_page=page_info_data["hasPreviousPage"],
            start_cursor=page_info_data.get("startCursor"),
            end_cursor=page_info_data.get("endCursor"),
        )

        return DiscussionsResponse(discussions=discussions, pagination=pagination)

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
        query = """
        query($discussionId: ID!, $first: Int, $after: String) {
            node(id: $discussionId) {
                ... on Discussion {
                    comments(first: $first, after: $after) {
                        nodes {
                            id
                            body
                            bodyHTML
                            createdAt
                            updatedAt
                            author {
                                login
                                avatarUrl
                                url
                            }
                            replyTo {
                                id
                            }
                            isAnswer
                        }
                    }
                }
            }
        }
        """

        variables = {
            "discussionId": discussion_id,
            "first": first,
            "after": after,
        }

        data = self._make_request(query, variables)
        discussion_data = data["data"]["node"]

        if not discussion_data:
            raise NotFoundError(f"Discussion with ID {discussion_id} not found")

        comments_data = discussion_data["comments"]["nodes"]

        comments = []
        for comment_data in comments_data:
            comment = self._parse_comment(comment_data)
            comments.append(comment)

        return comments

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
        mutation = """
        mutation($input: AddDiscussionCommentInput!) {
            addDiscussionComment(input: $input) {
                clientMutationId
                comment {
                    id
                    body
                    bodyHTML
                    createdAt
                    updatedAt
                    author {
                        login
                        avatarUrl
                        url
                    }
                    replyTo {
                        id
                    }
                    isAnswer
                }
            }
        }
        """

        variables = {
            "input": {
                "body": body,
                "discussionId": discussion_id,
            }
        }

        if reply_to_id:
            variables["input"]["replyToId"] = reply_to_id
        if client_mutation_id:
            variables["input"]["clientMutationId"] = client_mutation_id

        data = self._make_request(mutation, variables)
        comment_data = data["data"]["addDiscussionComment"]["comment"]

        return self._parse_comment(comment_data)

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
        query = """
        query($owner: String!, $repo: String!, $first: Int, $after: String) {
            repository(owner: $owner, name: $repo) {
                discussionCategories(first: $first, after: $after) {
                    nodes {
                        id
                        name
                        description
                        emoji
                        isAnswerable
                    }
                }
            }
        }
        """

        variables = {
            "owner": owner,
            "repo": repo,
            "first": first,
            "after": after,
        }

        data = self._make_request(query, variables)
        categories_data = data["data"]["repository"]["discussionCategories"]["nodes"]

        categories = []
        for category_data in categories_data:
            category = self._parse_category(category_data)
            if category:  # parse_category can return None
                categories.append(category)

        return categories

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
        query = """
        query($owner: String!, $repo: String!, $first: Int, $after: String) {
            repository(owner: $owner, name: $repo) {
                pinnedDiscussions(first: $first, after: $after) {
                    nodes {
                        id
                        number
                        title
                        body
                        bodyHTML
                        createdAt
                        updatedAt
                        author {
                            login
                            avatarUrl
                            url
                        }
                        category {
                            id
                            name
                            description
                            emoji
                            isAnswerable
                        }
                        comments {
                            totalCount
                        }
                        isAnswered
                        isLocked
                        isPinned
                        url
                    }
                }
            }
        }
        """

        variables = {
            "owner": owner,
            "repo": repo,
            "first": first,
            "after": after,
        }

        data = self._make_request(query, variables)
        discussions_data = data["data"]["repository"]["pinnedDiscussions"]["nodes"]

        discussions = []
        for discussion_data in discussions_data:
            discussion = self._parse_discussion(discussion_data)
            discussions.append(discussion)

        return discussions

    def get_discussion(self, owner: str, repo: str, number: int) -> Discussion:
        """Get a specific discussion by number.

        Args:
            owner: Repository owner
            repo: Repository name
            number: Discussion number

        Returns:
            Discussion object
        """
        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
            repository(owner: $owner, name: $repo) {
                discussion(number: $number) {
                    id
                    number
                    title
                    body
                    bodyHTML
                    createdAt
                    updatedAt
                    author {
                        login
                        avatarUrl
                        url
                    }
                    category {
                        id
                        name
                        description
                        emoji
                        isAnswerable
                    }
                    comments {
                        totalCount
                    }
                    isAnswered
                    isLocked
                    isPinned
                    url
                }
            }
        }
        """

        variables = {
            "owner": owner,
            "repo": repo,
            "number": number,
        }

        data = self._make_request(query, variables)
        discussion_data = data["data"]["repository"]["discussion"]

        if not discussion_data:
            raise NotFoundError(f"Discussion #{number} not found in {owner}/{repo}")

        return self._parse_discussion(discussion_data)

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
        mutation = """
        mutation($input: CreateDiscussionInput!) {
            createDiscussion(input: $input) {
                clientMutationId
                discussion {
                    id
                    number
                    title
                    body
                    bodyHTML
                    createdAt
                    updatedAt
                    author {
                        login
                        avatarUrl
                        url
                    }
                    category {
                        id
                        name
                        description
                        emoji
                        isAnswerable
                    }
                    comments {
                        totalCount
                    }
                    isAnswered
                    isLocked
                    isPinned
                    url
                }
            }
        }
        """

        variables = {
            "input": {
                "repositoryId": repository_id,
                "categoryId": category_id,
                "title": title,
                "body": body,
            }
        }

        if client_mutation_id:
            variables["input"]["clientMutationId"] = client_mutation_id

        data = self._make_request(mutation, variables)
        discussion_data = data["data"]["createDiscussion"]["discussion"]

        return self._parse_discussion(discussion_data)

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
            response = self.get_discussions(
                owner=owner,
                repo=repo,
                first=first,
                after=cursor,
                category_id=category_id,
                answered=answered,
                order_by=order_by,
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
        return self._make_request(query, variables, operation_name)
