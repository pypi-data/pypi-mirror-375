#!/usr/bin/env python3
"""
Basic usage example for GitHub Discussions GraphQL client.

This example demonstrates how to use the GitHub Discussions GraphQL client
to interact with discussions on GitHub repositories.
"""

import os
import sys

from github_discussions import GitHubDiscussionsClient
from github_discussions.exceptions import GitHubGraphQLError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main() -> None:
    """Main example function."""
    # Get GitHub token from environment variable
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Please set GITHUB_TOKEN environment variable")
        print("You can get a token from: https://github.com/settings/tokens")
        return

    # Initialize the client
    client = GitHubDiscussionsClient(token=token)

    try:
        # Example 1: Get rate limit status
        print("=== Rate Limit Status ===")
        rate_limit = client.get_rate_limit_status()
        print(f"Limit: {rate_limit.limit}")
        print(f"Remaining: {rate_limit.remaining}")
        print(f"Used: {rate_limit.used}")
        print(f"Reset At: {rate_limit.reset_at}")
        print()

        # Example 2: Get discussions from a repository
        print("=== Getting Discussions ===")
        owner = "octocat"  # Replace with actual owner
        repo = "Hello-World"  # Replace with actual repository

        discussions = client.get_discussions(owner, repo, first=5)
        print(f"Found {len(discussions)} discussions")

        for discussion in discussions:
            print(f"- #{discussion.number}: {discussion.title}")
            author_login = discussion.author.login if discussion.author else "Unknown"
            print(f"  Author: {author_login}")
            print(f"  Comments: {discussion.comments_count}")
            print(f"  Answered: {discussion.is_answered}")
            print(f"  Created: {discussion.created_at}")
            print()

        # Example 3: Get a specific discussion
        if discussions:
            print("=== Getting Specific Discussion ===")
            discussion_number = discussions[0].number
            discussion = client.get_discussion(owner, repo, discussion_number)
            print(f"Discussion #{discussion.number}: {discussion.title}")
            print(f"Body: {discussion.body[:200]}...")
            print()

            # Example 4: Get comments for the discussion
            print("=== Getting Discussion Comments ===")
            comments = client.get_discussion_comments(discussion.id, first=3)
            print(f"Found {len(comments)} comments")

            for comment in comments:
                comment_author = comment.author.login if comment.author else "Unknown"
                print(f"- Comment by {comment_author}")
                print(f"  Created: {comment.created_at}")
                print(f"  Is Answer: {comment.is_answer}")
                print(f"  Body: {comment.body[:100]}...")
                print()

        # Example 5: Get discussion categories
        print("=== Getting Discussion Categories ===")
        categories = client.get_discussion_categories(owner, repo)
        print(f"Found {len(categories)} categories")

        for category in categories:
            print(f"- {category.name}: {category.description}")
            print(f"  Emoji: {category.emoji}")
            print(f"  Answerable: {category.is_answerable}")
            print()

        # Example 6: Create a new discussion (uncomment to test)
        # print("=== Creating New Discussion ===")
        # This would require actual repository ID and category ID
        # new_discussion = client.create_discussion(
        #     repository_id="R_kgDOAHz1OX",  # Replace with actual repo ID
        #     category_id="DIC_kwDOAHz1OX4CW5wG",  # Replace with actual category ID
        #     title="Test Discussion from API",
        #     body="This is a test discussion created via the GraphQL API."
        # )
        # print(f"Created discussion: {new_discussion.title}")

    except GitHubGraphQLError as e:
        print(f"GitHub API Error: {e}")
        if hasattr(e, "errors"):
            for error in e.errors:
                print(f"  - {error.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def async_example() -> None:
    """Async version of the example."""
    import asyncio

    from github_discussions import AsyncGitHubDiscussionsClient

    async def run_async_example() -> None:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("Please set GITHUB_TOKEN environment variable")
            return

        async with AsyncGitHubDiscussionsClient(token=token) as client:
            try:
                # Get discussions asynchronously
                discussions = await client.get_discussions(
                    "octocat", "Hello-World", first=3
                )
                print(f"Found {len(discussions)} discussions asynchronously")

                for discussion in discussions:
                    print(f"- {discussion.title}")

            except GitHubGraphQLError as e:
                print(f"GitHub API Error: {e}")

    # Run the async example
    print("=== Async Example ===")
    asyncio.run(run_async_example())


if __name__ == "__main__":
    print("GitHub Discussions GraphQL Client - Basic Usage Example")
    print("=" * 60)

    main()

    print("\n" + "=" * 60)
    async_example()

    print("\nExample completed!")
