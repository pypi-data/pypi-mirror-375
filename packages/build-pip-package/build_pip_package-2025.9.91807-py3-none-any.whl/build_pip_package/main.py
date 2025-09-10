"""
Main module for build_pip_package functionality.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from glob import glob


import json
import base64
import requests
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from py_llm7_code import generate_package_with_llm7
from setup_py_gen import generate_setup_py_from_llm
from readme_llm7_gen import generate_readme_from_llm
from langchain_llm7 import ChatLLM7
from langchain_core.language_models import BaseChatModel


GITHUB_API = "https://api.github.com"


def _write_files_to_dir(base_dir: Path, files: Dict[str, str]) -> None:
    for rel_path, content in files.items():
        p = base_dir / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def _run(cmd: list[str], *, cwd: Path, env: Optional[dict] = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _build_and_publish_with_twine(
    *,
    files: Dict[str, str],
    pypi_token: str,
) -> Dict[str, object]:
    """
    Writes `files` into a temp dir, runs:
      python -m pip install -U setuptools wheel twine
      python setup.py sdist bdist_wheel
      python -m twine upload --repository pypi dist/*
    Returns a dict with success flag and per-step logs.
    """
    logs: list[dict[str, object]] = []
    result: Dict[str, object] = {"success": False, "logs": logs}

    if not pypi_token:
        result["logs"].append({"error": "Missing pypi_token"})
        return result

    with tempfile.TemporaryDirectory(prefix="pkg_build_") as td:
        base = Path(td)
        _write_files_to_dir(base, files)

        # Ensure build tooling is present
        code, out, err = _run(
            [sys.executable, "-m", "pip", "install", "-U", "setuptools", "wheel", "twine"],
            cwd=base,
        )
        logs.append({"step": "install_tools", "cmd": "pip install -U setuptools wheel twine", "rc": code, "stdout": out, "stderr": err})
        if code != 0:
            return result

        # sdist + wheel
        code, out, err = _run([sys.executable, "setup.py", "sdist", "bdist_wheel"], cwd=base)
        logs.append({"step": "build", "cmd": "python setup.py sdist bdist_wheel", "rc": code, "stdout": out, "stderr": err})
        if code != 0:
            return result

        dist_dir = base / "dist"
        dist_files = sorted(glob(str(dist_dir / "*")))
        if not dist_files:
            logs.append({"step": "build_check", "error": "No artifacts in dist/ after build"})
            return result

        # Twine upload (use env to avoid exposing token in args)
        env = os.environ.copy()
        env["TWINE_USERNAME"] = "__token__"
        env["TWINE_PASSWORD"] = pypi_token

        cmd = [sys.executable, "-m", "twine", "upload", "--repository", "pypi", *dist_files]
        code, out, err = _run(cmd, cwd=base, env=env)
        logs.append({"step": "twine_upload", "cmd": " ".join(cmd), "rc": code, "stdout": out, "stderr": err})
        if code != 0:
            return result

        result["success"] = True
        result["artifacts"] = dist_files
        return result

def _gh_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _parse_owner_repo_from_url(url: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Accepts forms like:
      https://github.com/owner/repo
      https://github.com/owner/repo.git
      github.com/owner/repo
    Returns (owner, repo) or (None, None) if parsing fails.
    """
    if not url:
        return None, None

    u = url if "://" in url else f"https://{url}"
    parsed = urlparse(u)
    path = parsed.path.strip("/")

    if not path:
        return None, None

    parts = path.split("/")
    if len(parts) < 2:
        return None, None

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def _gh_get_authenticated_user(token: str) -> str:
    resp = requests.get(f"{GITHUB_API}/user", headers=_gh_headers(token), timeout=30)
    resp.raise_for_status()
    return resp.json()["login"]


def _gh_repo_exists(token: str, owner: str, repo: str) -> bool:
    resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}", headers=_gh_headers(token), timeout=30
    )
    if resp.status_code == 200:
        return True
    if resp.status_code == 404:
        return False
    resp.raise_for_status()
    return False


def _sanitize_repo_description(description: Optional[str]) -> str:
    if not description:
        return ""
    # Replace newlines/tabs, strip C0 controls + DEL, collapse whitespace, cap length
    s = (
        description.replace("\r", " ")
        .replace("\n", " ")
        .replace("\t", " ")
    )
    s = "".join(ch for ch in s if ord(ch) >= 32 and ord(ch) != 127)
    s = " ".join(s.split())
    return s[:512]



def _gh_create_repo(
    token: str,
    owner: str,
    repo: str,
    description: str,
    is_org: bool,
    private: bool = False,
) -> Dict:
    """
    Creates repo under user (/user/repos) or org (/orgs/{org}/repos).
    Uses auto_init=True to ensure default branch exists.

    Idempotent: if GitHub returns 422, we check if the repo already exists and
    return its metadata instead of erroring.
    """
    payload = {
        "name": repo,
        "description": _sanitize_repo_description(description),
        "private": private,
        "auto_init": True,
    }

    url = f"{GITHUB_API}/orgs/{owner}/repos" if is_org else f"{GITHUB_API}/user/repos"
    resp = requests.post(url, headers=_gh_headers(token), json=payload, timeout=60)

    if resp.status_code in (200, 201):
        # proceed to canonical GET below
        pass
    elif resp.status_code == 422:
        # Treat as "already exists" if we can GET it
        check = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}", headers=_gh_headers(token), timeout=30
        )
        if check.status_code == 200:
            return check.json()
        # Otherwise raise with JSON details for easier debugging
        try:
            detail = resp.json()
        except Exception:
            detail = {"text": resp.text}
        raise requests.HTTPError(f"422 creating repo: {detail}", response=resp)
    else:
        resp.raise_for_status()

    repo_resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}", headers=_gh_headers(token), timeout=30
    )
    repo_resp.raise_for_status()
    return repo_resp.json()



def _gh_get_file_sha_if_exists(
    token: str, owner: str, repo: str, path: str, ref: Optional[str] = None
) -> Optional[str]:
    params = {"ref": ref} if ref else None
    resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
        headers=_gh_headers(token),
        params=params,
        timeout=30,
    )
    if resp.status_code == 200:
        return resp.json().get("sha")
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return None


def _gh_upsert_file(
    token: str,
    owner: str,
    repo: str,
    path: str,
    content_text: str,
    message: str,
    author_name: str,
    author_email: str,
    branch: Optional[str] = None,
) -> Dict:
    """
    Creates or updates a file at `path` with `content_text`.
    """
    sha = _gh_get_file_sha_if_exists(token, owner, repo, path, ref=branch)
    b64 = base64.b64encode(content_text.encode("utf-8")).decode("ascii")

    payload = {
        "message": message,
        "content": b64,
        "committer": {"name": author_name, "email": author_email},
    }
    if branch:
        payload["branch"] = branch
    if sha:
        payload["sha"] = sha

    resp = requests.put(
        f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
        headers=_gh_headers(token),
        data=json.dumps(payload),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def _default_python_gitignore() -> str:
    return (
        "# Byte-compiled / optimized / DLL files\n"
        "__pycache__/\n*.py[cod]\n*$py.class\n\n"
        "# Distribution / packaging\n"
        ".Python\nbuild/\ndist/\n*.egg-info/\n.eggs/\n"
        "pip-wheel-metadata/\n\n"
        "# Virtual environments\n"
        "venv/\n.env\n.venv\n\n"
        "# OS\n.DS_Store\nThumbs.db\n\n"
        "# Tools\n.pytest_cache/\n.mypy_cache/\n.pytype/\n.coverage\nhtmlcov/\n"
        ".hypothesis/\n.ipynb_checkpoints/\n"
        ".vscode/\n.idea/\n*.swp\n"
        "env/\nENV/\n"
        "*.env\n*.venv\n.venv/\nenv.bak/\nvenv.bak/\n"
        "build/\n"  # sometimes used for build dirs
        "dist/\n"  # sometimes used for dist dirs
        "*.egg-info/\n"
        ".eggs/\n"
        "dist*/\n"
        "venv*/\n"
    )


def _owner_is_org(token: str, owner: str) -> bool:
    """
    Determine if `owner` is an org. If not found, assume user.
    """
    resp = requests.get(f"{GITHUB_API}/users/{owner}", headers=_gh_headers(token), timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        # type can be "User" or "Organization"
        return data.get("type") == "Organization"
    # On error, fall back to user.
    return False


def _ensure_repo_and_push_files(
    *,
    github_token: str,
    git_repo_link: Optional[str],
    package_name: str,
    description: str,
    author_full_name: str,
    author_email: str,
    files: Dict[str, str],
    private: bool = False,
    branch: Optional[str] = None,
) -> Dict[str, str]:
    authed_login = _gh_get_authenticated_user(github_token)
    owner_from_url, repo_from_url = _parse_owner_repo_from_url(git_repo_link)

    owner = owner_from_url or authed_login
    repo = repo_from_url or package_name

    # If an explicit user owner is provided and it's not us, fail fast.
    # (Creating under another *user* account is not possible via /user/repos.)
    if owner_from_url and owner != authed_login:
        # Allow orgs, disallow other users.
        if not _owner_is_org(github_token, owner):
            raise PermissionError(
                f"Cannot create repo under user '{owner}' with a token for '{authed_login}'."
            )

    exists = _gh_repo_exists(github_token, owner, repo)
    if not exists:
        is_org = _owner_is_org(github_token, owner)
        created = _gh_create_repo(
            github_token, owner, repo, description=description, is_org=is_org, private=private
        )
        default_branch = created.get("default_branch") or "main"
        html_url = created.get("html_url")
        ssh_url = created.get("ssh_url")
        clone_url = created.get("clone_url")
    else:
        meta = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}", headers=_gh_headers(github_token), timeout=30
        )
        meta.raise_for_status()
        data = meta.json()
        default_branch = data.get("default_branch") or "main"
        html_url = data.get("html_url")
        ssh_url = data.get("ssh_url")
        clone_url = data.get("clone_url")

    target_branch = branch or default_branch

    for path, content in files.items():
        _gh_upsert_file(
            github_token,
            owner,
            repo,
            path,
            content,
            message=f"Add/update {path}",
            author_name=author_full_name,
            author_email=author_email,
            branch=target_branch,
        )

    return {
        "owner": owner,
        "repo": repo,
        "html_url": html_url,
        "ssh_url": ssh_url,
        "clone_url": clone_url,
        "default_branch": target_branch,
    }


def build_pip_package(
    package_name: str,
    text_description: str,
    author_full_name: str,
    author_email: str,
    git_repo_link: str,
    licence_description: str,
    github_token: str,
    pypi_token: Optional[str] = None,
    llm: Optional[ChatLLM7] = None,
):
    """
    Build a pip package using LLM7 and related tools.
    
    Args:
        text_description (str): Description of the package to build
        author_full_name (str): Full name of the package author
        author_email (str): Email address of the package author
        git_repo_link (str): Git repository link for the package
        licence_description (str): License description for the package
        github_token (str): GitHub token for authentication
        
    Returns:
        Package build result or status
    """
    # TODO: Implement the actual package building logic
    # This is a placeholder implementation
    
    # Generate package code using LLM7
    package_code = generate_package_with_llm7(
        llm=llm,
        package_name=package_name,
        pip_packages=[],
        allowed_imports=[],
        spec_text=text_description + "\n" + licence_description,
    )
    
    # Generate setup.py using LLM
    setup_py_content = generate_setup_py_from_llm(
        llm=llm,
        custom_text=package_code["package_name"] + text_description + package_code["init_py_code"] + \
        "License: " + licence_description + "\n" +
        """
The example of setup.py is:
from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='mdextractor',
    version='2025.4.231259',
    author='Eugene Evstafev',
    author_email='hi@eugene.plus',
    description='Extract Markdown code blocks from text strings.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/mdextractor',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT',
    tests_require=['unittest'],
    test_suite='test',
)
        """,
        author=author_full_name,
        author_email=author_email,
        repo_url=git_repo_link,
    )
    
    # Generate README using LLM
    readme_content = generate_readme_from_llm(
        llm=llm,
        package_text=package_code["package_name"] + text_description + package_code["init_py_code"] + \
        "License: " + licence_description + "\n" + """
The example of README.md is:
[![PyPI version](https://badge.fury.io/py/mdextractor.svg)](https://badge.fury.io/py/mdextractor)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/mdextractor)](https://pepy.tech/project/mdextractor)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# mdextractor

`mdextractor` is a Python package designed for extracting code blocks from Markdown text. It efficiently identifies blocks enclosed in triple backticks (\`\`\`), optionally preceded by language identifiers, and extracts their contents.

## Installation

To install `mdextractor`, use pip:

```bash
pip install mdextractor
```

## Usage

Using `mdextractor` is straightforward. Here's an example:

```python
from mdextractor import extract_md_blocks

text = '''
\`\`\`python
print("Hello, Markdown!")
\`\`\`
'''

blocks = extract_md_blocks(text)
print(blocks)
# Output: ['print("Hello, Markdown!")']
```

This package is useful in various applications where extracting code or preformatted text from Markdown is necessary.

## Features

- Efficient extraction of Markdown code blocks.
- Supports language specifiers following the opening backticks.
- Works with multi-line and single-line code blocks.
- Simple API with a single function call.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/chigwell/mdextractor/issues).

## License

`mdextractor` is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).


====
you can use badges (just replace with project number) and author linkedin link (the same)
""",
        author_name=author_full_name,
        author_email=author_email,
        repo_link=git_repo_link
    )


    '''print(package_code["package_name"])
    print(package_code["init_py_code"])
    print(setup_py_content)
    print(readme_content)
    exit()'''

    if (
            package_code["package_name"] is not None
            and package_code["init_py_code"] is not None
            and setup_py_content is not None
            and readme_content is not None
    ):
        pkg_name = package_code["package_name"]
        pkg_dir = pkg_name.replace("-", "_")

        files_to_commit: Dict[str, str] = {
            "README.md": readme_content,
            "setup.py": setup_py_content,
            f"{pkg_dir}/__init__.py": package_code["init_py_code"],
            "LICENSE": (licence_description or "").strip() or "SEE LICENSE IN REPO",
            ".gitignore": _default_python_gitignore(),
        }

        repo_meta = _ensure_repo_and_push_files(
            github_token=github_token,
            git_repo_link=git_repo_link,
            package_name=pkg_name,
            description=_sanitize_repo_description(text_description),
            author_full_name=author_full_name,
            author_email=author_email,
            files=files_to_commit,
            private=False,  # set True if you want a private repo
            branch=None,  # None => use default branch
        )
    else:
        repo_meta = {}

    pypi_result: Dict[str, object] = {}
    files_for_build: Dict[str, str] = locals().get("files_to_commit", {})

    if pypi_token and files_for_build:
        try:
            pypi_result = _build_and_publish_with_twine(
                files=files_for_build,
                pypi_token=pypi_token,
            )
        except Exception as e:
            pypi_result = {"success": False, "error": str(e)}

    return {
        "package_code": package_code,
        "setup_py": setup_py_content,
        "readme": readme_content,
        "repo": repo_meta,
        "pypi": pypi_result,
        "status": "success"
    }