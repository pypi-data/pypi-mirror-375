#!/usr/bin/env python3
import argparse
from pathlib import Path
from .core import bootstrap

def main():
    parser = argparse.ArgumentParser(description="Project bootstrapper")
    parser.add_argument("directory", nargs="?", default=".", help="Where to build the project")
    args = parser.parse_args()

    root = Path(args.directory).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    bootstrap(root)

if __name__ == "__main__":
    main()

