#!/usr/bin/env python3

import subprocess
import sys

from common import check_for_required_tools, maybe_run, run


def format_code() -> None:
    maybe_run(["gofmt", "-s", "-w", "."])
    run(["npx", "prettier", "--write", "."])
    run(["uvx", "ruff", "check", "--fix-only", "."])
    run(["uvx", "ruff", "format", "."])


def main() -> None:
    check_for_required_tools()
    try:
        format_code()
    except subprocess.CalledProcessError:
        sys.exit(1)


if __name__ == "__main__":
    main()
