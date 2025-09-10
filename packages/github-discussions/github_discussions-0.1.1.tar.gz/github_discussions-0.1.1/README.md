# GitHub Discussions GraphQL Client

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/github-discussions.svg)](https://badge.fury.io/py/github-discussions)

A comprehensive Python package for interacting with GitHub Discussions using the GraphQL API. This package provides a clean, type-safe interface for managing discussions, comments, and related functionality on GitHub.

This project is generated 99% by grok-code-fast-1, there may be missing, incomplete or incorrect features. Contributors welcome!

## Features

- 🔐 **Secure Authentication**: Support for personal access tokens and GitHub Apps
- 📝 **Full Discussion Management**: Create, read, update, and delete discussions
- 💬 **Comment Management**: Handle discussion comments with full CRUD operations
- 🏷️ **Category Support**: Work with discussion categories
- ⭐ **Pin/Unpin Discussions**: Manage pinned discussions
- 🎯 **Answer Marking**: Mark comments as answers
- 📊 **Advanced Pagination**: Fixed cursor-based pagination with automatic iteration
- 🔍 **Search Integration**: Search discussions using GitHub's search API
- 🛡️ **Type Safety**: Full type hints and Pydantic models
- ⚡ **Async Support**: Optional async/await support
- 🧪 **Well Tested**: "Comprehensive" test coverage, the llm is a bit optimistic here.
- 🏗️ **Clean Architecture**: Refactored to eliminate code duplication between sync/async clients

## Installation

```bash
pip install github-discussions
```

## Quick Start

```python
from github_discussions import GitHubDiscussionsClient

# Initialize the client
client = GitHubDiscussionsClient(token="your_github_token")

# Get discussions for a repository
discussions = client.get_discussions(
    owner="octocat",
    repo="Hello-World",
    first=10
)

# Create a new discussion
discussion = client.create_discussion(
    repository_id="R_kgDOAHz1OX",
    category_id="DIC_kwDOAHz1OX4CW5wG",
    title="My New Discussion",
    body="This is the content of my discussion"
)

# Add a comment to a discussion
comment = client.add_discussion_comment(
    discussion_id="D_kwDOAHz1OX4uYAah",
    body="This is my comment"
)
```

## Authentication

The package supports multiple authentication methods:

### Personal Access Token

```python
from github_discussions import GitHubDiscussionsClient

client = GitHubDiscussionsClient(token="ghp_your_token_here")
```

### GitHub App

```python
from github_discussions import GitHubDiscussionsClient

client = GitHubDiscussionsClient(
    token="installation_token",
    app_id="your_app_id"
)
```


## Core Features

### Managing Discussions

```python
# Get all discussions
discussions = client.get_discussions("owner", "repo")

# Get a specific discussion
discussion = client.get_discussion("owner", "repo", number=1)

# Create a discussion
new_discussion = client.create_discussion(
    repository_id="repo_id",
    category_id="category_id",
    title="Discussion Title",
    body="Discussion content"
)

# Update a discussion
updated = client.update_discussion(
    discussion_id="discussion_id",
    title="New Title",
    body="Updated content"
)

# Delete a discussion
client.delete_discussion("discussion_id")
```

### Working with Comments

```python
# Get comments for a discussion
comments = client.get_discussion_comments("discussion_id")

# Add a comment
comment = client.add_discussion_comment(
    discussion_id="discussion_id",
    body="Comment content",
    reply_to_id="parent_comment_id"  # Optional
)

# Update a comment
updated_comment = client.update_discussion_comment(
    comment_id="comment_id",
    body="Updated comment content"
)

# Delete a comment
client.delete_discussion_comment("comment_id")

# Mark comment as answer
client.mark_comment_as_answer("comment_id")

# Unmark comment as answer
client.unmark_comment_as_answer("comment_id")
```

### Managing Categories

```python
# Get discussion categories
categories = client.get_discussion_categories("owner", "repo")

# Create a category (if you have admin permissions)
category = client.create_discussion_category(
    repository_id="repo_id",
    name="New Category",
    description="Category description",
    emoji="🎯"
)
```

### Pinned Discussions

```python
# Get pinned discussions
pinned = client.get_pinned_discussions("owner", "repo")

# Pin a discussion
client.pin_discussion("discussion_id")

# Unpin a discussion
client.unpin_discussion("discussion_id")
```

## Advanced Usage

### Async Support

```python
import asyncio
from github_discussions import AsyncGitHubDiscussionsClient

async def main():
    async with AsyncGitHubDiscussionsClient(token="your_token") as client:
        discussions = await client.get_discussions("owner", "repo")
        print(discussions)

asyncio.run(main())
```

### Custom GraphQL Queries

```python
# Execute custom GraphQL queries
result = client.execute_query("""
    query($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
            discussions(first: 10) {
                nodes {
                    id
                    title
                    createdAt
                    author {
                        login
                    }
                }
            }
        }
    }
""", variables={"owner": "octocat", "repo": "Hello-World"})
```

### Pagination

```python
# Automatic pagination handling
all_discussions = []
for page in client.get_discussions_paginated("owner", "repo"):
    all_discussions.extend(page)
```

### Error Handling

```python
from github_discussions import GitHubGraphQLError, RateLimitError

try:
    discussion = client.get_discussion("owner", "repo", 1)
except RateLimitError as e:
    print(f"Rate limited. Reset at: {e.reset_at}")
    # Wait or retry with backoff
except GitHubGraphQLError as e:
    print(f"GraphQL error: {e.message}")
    # Handle GraphQL-specific errors
except Exception as e:
    print(f"Other error: {e}")
```

## Architecture

### Clean Code Design

The package has been refactored to eliminate code duplication between synchronous and asynchronous clients:

- **Base Client**: `BaseGitHubDiscussionsClient` contains all shared functionality
- **Sync Client**: `GitHubDiscussionsClient` inherits from base and adds synchronous HTTP requests
- **Async Client**: `AsyncGitHubDiscussionsClient` inherits from base and adds asynchronous HTTP requests

This design ensures:
- ✅ **DRY Principle**: No code duplication between sync and async implementations
- ✅ **Maintainability**: Changes to core logic only need to be made in one place
- ✅ **Consistency**: Both clients have identical functionality and behavior
- ✅ **Type Safety**: Shared type definitions and validation

## Configuration

### Rate Limiting

The client automatically handles GitHub's rate limits:

```python
# Check current rate limit status
status = client.get_rate_limit_status()
print(f"Remaining: {status['remaining']}, Reset: {status['reset_at']}")

# Custom retry configuration
client = GitHubDiscussionsClient(
    token="your_token",
    max_retries=3,
    retry_backoff=2.0
)
```

### Timeouts

```python
client = GitHubDiscussionsClient(
    token="your_token",
    timeout=30.0  # 30 second timeout
)
```

## API Reference

For complete API documentation, see the [API Reference](https://github.com/Declytic/github-discussions/docs/api.md).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Declytic/github-discussions.git
cd github-discussions

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (recommended)
pre-commit install

# Run tests
pytest

# Run linting
black .
isort .
flake8 .
mypy .
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=github_discussions

# Run specific test
pytest tests/test_discussions.py::test_get_discussions
```

## CI/CD

This project uses GitHub Actions for continuous integration and deployment. The following workflows are configured:

### Workflows

- **CI** (`.github/workflows/ci.yml`): Runs tests on multiple Python versions (3.8-3.12) across different operating systems (Ubuntu, Windows, macOS)
- **Code Quality** (`.github/workflows/code-quality.yml`): Runs linting, formatting checks, and type checking
- **Pre-commit** (`.github/workflows/pre-commit.yml`): Runs pre-commit hooks to ensure code quality
- **Security** (`.github/workflows/security.yml`): Scans for security vulnerabilities and dependency issues
- **Release** (`.github/workflows/release.yml`): Builds and publishes the package to PyPI when a release is created
- **Development** (`.github/workflows/dev.yml`): Manual workflow for development tasks (can be triggered manually)

### Automated Checks

The following checks run automatically on every push and pull request:

- **Testing**: Unit tests with pytest across multiple Python versions
- **Code Coverage**: Coverage reporting with Codecov integration
- **Linting**: flake8 for code style and error detection
- **Type Checking**: mypy for static type analysis
- **Formatting**: black and isort for code formatting
- **Security**: Bandit for security linting, Safety for dependency vulnerabilities
- **Pre-commit**: Automated code quality checks

### Releasing

To release a new version:

1. **Automatic Release**: Create a new release on GitHub with a version tag (e.g., `v1.0.0`)
2. **Manual Release**: Use the "Development" workflow with the "build" task, then manually upload to PyPI

The release workflow will:
- Build the package using `python -m build`
- Run final tests
- Publish to PyPI using trusted publishing
- Optionally deploy documentation to GitHub Pages

### Dependencies

Dependencies are automatically updated weekly using Dependabot:
- Python dependencies from `pyproject.toml`
- GitHub Actions versions
- Security updates with priority

### Pre-commit Hooks

Pre-commit hooks are configured to run locally and in CI:

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

Configured hooks include:
- Code formatting (black, isort)
- Linting (flake8, mypy, bandit)
- General file checks (trailing whitespace, large files, etc.)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](https://github.com/Declytic/github-discussions/docs/)
- 🐛 [Issue Tracker](https://github.com/Declytic/github-discussions/issues)
- 💬 [Discussions](https://github.com/Declytic/github-discussions/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
