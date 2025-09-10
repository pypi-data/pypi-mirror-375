import shutil
import subprocess
import sys


def run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=capture, text=capture)


def maybe_run(cmd: list[str]) -> None:
    if not shutil.which(cmd[0]):
        return
    run(cmd)


def check_for_required_tools() -> None:
    """Check that required tools are available, exit if not."""
    missing = []
    if not shutil.which("uvx"):
        missing.append("uvx")
    if not shutil.which("npx"):
        missing.append("npx")
    if missing:
        print(f"Error: Required tools not found: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def get_files_by_ext(ext: str, all_files: bool) -> set[str]:
    def _git(cmd: list[str]) -> set[str]:
        stdout = run(["git"] + cmd, capture=True).stdout.strip()
        return set(stdout.splitlines()) if stdout else set()

    if all_files:
        # All non-deleted files.
        files = _git(["ls-files", "-c", "-o", "--exclude-standard", f"*.{ext}"])
        deleted = _git(["ls-files", "-d"])
        return files - deleted
    else:
        # New or modified files relative to main branch, and untracked files.
        changed = _git(["diff", "--name-only", "--diff-filter=d", "main"])
        changed = {x for x in changed if x.endswith(f".{ext}")}
        untracked = _git(["ls-files", "-o", "--exclude-standard", f"*.{ext}"])
        return changed | untracked
