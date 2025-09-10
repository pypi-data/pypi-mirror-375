#!/usr/bin/env python3
"""
Example demonstrating how to use GitHub Discussions with xAI function calling.

This example shows how to:
1. Check if xAI dependencies are available
2. Use the xAI integration when available
3. Gracefully handle missing dependencies
"""

import os


def main() -> None:
    """Main example function."""
    print("🚀 GitHub Discussions xAI Integration Example")
    print("=" * 50)

    # Try to import the main package
    try:
        import github_discussions

        print("✅ GitHub Discussions package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import GitHub Discussions: {e}")
        return

    # Check if xAI functionality is available
    if (
        hasattr(github_discussions, "_XAI_AVAILABLE")
        and github_discussions._XAI_AVAILABLE
    ):
        print("✅ xAI dependencies are available!")
        print("🔧 You can use the full xAI integration")

        # Example of using the xAI functionality
        try:
            from github_discussions import GitHubDiscussionsAssistant  # noqa: F401
            from github_discussions import setup_github_discussions_tools

            # Set dummy tokens for demonstration
            # These are example values only, not real credentials
            os.environ["GITHUB_TOKEN"] = "demo_token"  # nosec B105
            os.environ["XAI_API_KEY"] = "demo_key"  # nosec B105

            # Setup tools
            tools = setup_github_discussions_tools("demo_token")
            print(f"✅ Setup {len(tools)} tools successfully")

            # Show available tools
            tool_names = [tool["function"]["name"] for tool in tools]
            print(f"🔧 Available tools: {', '.join(tool_names)}")

            print("\n💡 To use the interactive assistant:")
            print("   python -m github_discussions.xai_chat_integration")

        except Exception as e:
            print(f"❌ Error setting up xAI integration: {e}")
            print("💡 Make sure you have valid API keys set in environment variables")

    else:
        print("ℹ️  xAI dependencies are not installed")
        print("📦 To enable xAI function calling, install:")
        print("   pip install xai-sdk pydantic")
        print()
        print("🔧 You can still use the core GitHub Discussions functionality:")

        # Show core functionality
        try:
            from github_discussions import GitHubDiscussionsClient  # noqa: F401

            print("✅ Core GitHub Discussions client available")
            print("📖 Example usage:")
            print("   client = GitHubDiscussionsClient(token='your_token')")
            print("   discussions = client.get_discussions('owner', 'repo')")

        except Exception as e:
            print(f"❌ Error with core functionality: {e}")

    print("\n🎯 Summary:")
    print("- Core GitHub Discussions functionality: ✅ Always available")
    print("- xAI function calling: ✅ Available if xai-sdk and pydantic are installed")
    print("- Interactive AI assistant: ✅ Available with full xAI integration")


if __name__ == "__main__":
    main()
