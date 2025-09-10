#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path

from common import check_for_required_tools, get_files_by_ext, maybe_run, run


def lint_code(all_files: bool) -> None:
    if (Path.cwd() / "go.mod").exists():
        maybe_run(["go", "vet", "./..."])
    run(["npx", "prettier", "--check", "."])
    run(["npx", "jshint", "."])
    run(["uvx", "ruff", "check", "."])
    run(["uvx", "ruff", "format", "--check", "."])
    py_files = list(get_files_by_ext("py", all_files))
    if py_files:
        run(["uvx", "pyright"] + py_files)


def main() -> None:
    check_for_required_tools()
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all-files", action="store_true")
    args = parser.parse_args()
    try:
        lint_code(args.all_files)
    except subprocess.CalledProcessError:
        sys.exit(1)


if __name__ == "__main__":
    main()
