[![PyPI version](https://badge.fury.io/py/build_pip_package.svg)](https://badge.fury.io/py/build_pip_package)
[![Downloads](https://static.pepy.tech/badge/build_pip_package)](https://pepy.tech/project/build_pip_package)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# build_pip_package

A Python package for building pip packages using LLM7 and related tools.

## Installation

```bash
pip install build_pip_package
```

## Usage

```python
from build_pip_package import build_pip_package

result = build_pip_package(
    text_description="A sample Python package",
    author_full_name="John Doe",
    author_email="john.doe@example.com", 
    git_repo_link="https://github.com/user/repo",
    licence_description="MIT License",
    github_token="your_github_token"
)
```

## Parameters

- `text_description` (str): Description of the package to build
- `author_full_name` (str): Full name of the package author
- `author_email` (str): Email address of the package author
- `git_repo_link` (str): Git repository link for the package
- `licence_description` (str): License description for the package
- `github_token` (str): GitHub token for authentication

## Dependencies

This package relies on the following dependencies:
- py_llm7_code
- setup_py_gen
- readme_llm7_gen
- langchain_llm7
- langchain_core