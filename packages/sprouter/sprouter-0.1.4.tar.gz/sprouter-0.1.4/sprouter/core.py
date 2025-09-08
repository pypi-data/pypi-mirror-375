#!/usr/bin/env python3
"""
Bootstrapper — Python Project Generator
---------------------------------------
Interactive script to scaffold a Python application, initialize Git,
configure Docker, set up GitHub, and prep for PyPI publishing.
"""

import os
import subprocess
import sys
from pathlib import Path
import venv
import shutil

# === Utility ===
def run_cmd(cmd, cwd=None, check=True):
    print(f"⚡ Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd, check=check)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if check:
            sys.exit(1)

def ask(prompt, default=None):
    val = input(f"{prompt} " + (f"[{default}] " if default else ""))
    return val.strip() or default

# === Virtualenv creation ===
def create_venv(root: Path):
    env_dir = root / ".venv"
    print("🐍 Creating virtual environment...")
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(env_dir)

    pip_path = env_dir / "bin" / "pip" if os.name != "nt" else env_dir / "Scripts" / "pip.exe"
    run_cmd([str(pip_path), "install", "--upgrade", "pip"])
    run_cmd([str(pip_path), "install", "pytest", "build", "twine"])

    print("\n✅ Virtualenv ready.")
    print(f"To activate: source {env_dir}/bin/activate  (Linux/macOS)")
    print(f"             {env_dir}\\Scripts\\activate    (Windows PowerShell)\n")

    return pip_path

# === Bootstrap Flow ===
def main():
    print("🚀 Python App Bootstrapper")

    # Interactive prompts
    app_name = ask("App name (no spaces):")
    description = ask("Description:", "My awesome Python app")
    author = ask("Author:", os.getenv("USER", ""))
    email = ask("Author email:")
    github_user = ask("GitHub username:")
    license_type = ask("License (MIT/Apache-2.0/etc.):", "MIT")

    root = Path(app_name)
    if root.exists():
        print(f"❌ Directory {root} already exists, aborting.")
        sys.exit(1)

    # === Directory structure ===
    print("📂 Creating directory structure...")
    (root / app_name).mkdir(parents=True)
    (root / "tests").mkdir()
    (root / ".github" / "workflows").mkdir(parents=True)

    # === Files ===
    (root / app_name / "__init__.py").write_text('__version__ = "0.1.0"\n')
    (root / "tests" / "test_basic.py").write_text("def test_placeholder():\n    assert True\n")
    (root / "requirements.txt").write_text("")
    (root / ".gitignore").write_text("__pycache__/\n*.pyc\n.env\n.venv\n*.egg-info/\n")
    (root / "README.md").write_text(f"# {app_name}\n\n{description}\n")
    (root / "Dockerfile").write_text(f"""\
FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "{app_name}"]
""")
    (root / ".dockerignore").write_text(".git\n__pycache__\n*.pyc\n.venv\n")

    # PyPI packaging (PEP 621 via pyproject.toml)
    (root / "pyproject.toml").write_text(f"""\
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{app_name}"
version = "0.1.0"
description = "{description}"
authors = [{{ name = "{author}", email = "{email}" }}]
license = {{ text = "{license_type}" }}
readme = "README.md"
requires-python = ">=3.9"
dependencies = []

[project.urls]
Homepage = "https://github.com/{github_user}/{app_name}"
""")

    # GitHub workflow for CI
    (root / ".github" / "workflows" / "ci.yml").write_text(f"""\
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
""")

    # === Git Init ===
    print("🌱 Initializing Git...")
    run_cmd(["git", "init"], cwd=root)
    run_cmd(["git", "add", "."], cwd=root)
    run_cmd(["git", "commit", "-m", "Initial commit"], cwd=root)

    # === Virtual Environment + Install Tools ===
    pip_path = create_venv(root)

    # Install local requirements (if any)
    run_cmd([str(pip_path), "install", "-r", "requirements.txt"], cwd=root)

    # === GitHub Repo Creation ===
    print("🐙 Setting up GitHub...")
    if shutil.which("gh"):
        run_cmd(["gh", "repo", "create", f"{github_user}/{app_name}", "--public", "--source=.", "--remote=origin", "--push"], cwd=root)
    else:
        print("⚠️ GitHub CLI (gh) not found. Install with: https://cli.github.com/")

    # Check for Docker
    if not shutil.which("docker"):
        print("⚠️ Docker not found. Install Docker Desktop / Engine.")

    # === Finish ===
    print(f"\n✅ Project {app_name} created successfully!")
    print(f"📂 Location: {root.resolve()}")
    print("Next steps:")
    print(f"  cd {app_name}")
    print("  source .venv/bin/activate   # activate virtualenv")
    print("  git push -u origin main")
    print("  docker build -t {app_name}:latest .")
    print("  python -m build && twine upload dist/*  (for PyPI)")

import keyring

def setup_github(root: Path, app_name: str):
    # Get GitHub user/org from keyring
    github_user = keyring.get_password("bootstrapper", "github_user")
    if not github_user:
        github_user = ask("GitHub username/org:")
        keyring.set_password("bootstrapper", "github_user", github_user)

    repo_ssh = f"git@github.com:{github_user}/{app_name}.git"

    # Init repo if not already done
    run_cmd(["git", "init"], cwd=root)
    run_cmd(["git", "add", "."], cwd=root)
    run_cmd(["git", "commit", "-m", "Initial commit"], cwd=root)

    # Set remote via SSH
    run_cmd(["git", "remote", "add", "origin", repo_ssh], cwd=root)

    print(f"🌐 Remote set to {repo_ssh}")

    # Try push
    try:
        run_cmd(["git", "push", "-u", "origin", "main"], cwd=root, check=True)
    except SystemExit:
        print("⚠️ Push failed. Make sure SSH key is added to GitHub and ssh-agent.")


if __name__ == "__main__":
    main()
