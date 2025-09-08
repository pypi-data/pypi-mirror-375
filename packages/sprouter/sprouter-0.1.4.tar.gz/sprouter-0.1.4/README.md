[![Chat-GPT-Image-Sep-7-2025-04-49-26-PM.png](https://i.postimg.cc/Wb7Y3wzj/Chat-GPT-Image-Sep-7-2025-04-49-26-PM.png)](https://postimg.cc/TppJNmnH)

# Sprouter

⚡ **Sprouter** is a simple project setup utility. It creates a Python virtual environment, installs dependencies, and prepares a working directory for development — all from a single CLI entrypoint.

Think of it as a one-shot “project scaffolder” that asks *where* you want your project to live and does the boring setup for you.

---

## ✨ Features

* Prompts for a target directory (or take it as a CLI argument).
* Builds a `.venv` virtual environment inside that directory.
* Installs all dependencies listed in `requirements.txt`.
* Ensures idempotency: if `.venv` already exists, it won’t overwrite it.
* Can be wired up with `pyproject.toml` to install as a global command.

---

## 🚀 Usage

Clone or download this repo, then run:

```bash
cd sprouter
python3 -m sprouter.cli ~/Projects/myapp
```

You’ll see:

```
⚡ Creating virtualenv at /home/you/Projects/myapp/.venv
⚡ Installing dependencies from requirements.txt
```

Activate your environment:

```bash
source ~/Projects/myapp/.venv/bin/activate
```

Windows (PowerShell):

```powershell
.\Projects\myapp\.venv\Scripts\Activate.ps1
```

---

## 🛠 Development

The code is split into two modules:

* `core.py` → core logic for environment creation & pip installs.
* `cli.py` → command-line interface, argument parsing, user prompts.

This separation makes it easy to import `sprouter.core` in other Python scripts without invoking the CLI.

---

## 📦 Packaging (optional)

To install `sprouter` as a system-wide command:

1. Add this to your `pyproject.toml`:

   ```toml
   [project]
   name = "sprouter"
   version = "0.1.0"
   dependencies = []

   [project.scripts]
   bootstrapper = "sprouter.cli:main"
   ```

2. Install in editable mode:

   ```bash
   pip install -e .
   ```

3. Now you can run:

   ```bash
   sprouter ~/Projects/myapp
   ```

---


## 📄 License

This project is distributed under a [custom license](LICENSE).  
Use freely, hack ruthlessly, share improvements — but ownership remains with the author.


