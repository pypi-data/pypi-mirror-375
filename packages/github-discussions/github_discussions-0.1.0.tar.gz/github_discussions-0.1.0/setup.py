"""Setup script for GitHub Discussions GraphQL client."""

from setuptools import find_packages, setup

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the contents of pyproject.toml for dependencies
try:
    import tomllib
except ImportError:
    import tomli as tomllib

with open("pyproject.toml", "rb") as f:
    pyproject_data = tomllib.load(f)

setup(
    name="github-discussions",
    version="0.1.0",
    author="Bill Schumacher",
    author_email="34168009+BillSchumacher@users.noreply.github.com",
    description=(
        "A Python package for interacting with GitHub Discussions " "using GraphQL API"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Declytic/github-discussions-graphql",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "types-requests>=2.25.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
    },
    package_data={
        "github_discussions": ["py.typed"],
    },
    include_package_data=True,
    zip_safe=False,
)
