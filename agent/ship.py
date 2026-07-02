"""Ship a validated fix: branch, commit, push, and open a real PR via gh."""

import subprocess


def _run(args: list[str], repo_path: str) -> str:
    proc = subprocess.run(args, cwd=repo_path, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout.strip()


def open_pr(
    repo_path: str,
    branch_name: str,
    commit_message: str,
    pr_title: str,
    pr_body: str,
    base: str = "main",
) -> str:
    """Create a branch, commit the working tree changes, push, and open a PR.
    Returns the PR URL."""
    _run(["git", "checkout", "-b", branch_name], repo_path)
    _run(["git", "add", "-A"], repo_path)
    _run(["git", "commit", "-m", commit_message], repo_path)
    _run(["git", "push", "-u", "origin", branch_name], repo_path)

    pr_url = _run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            pr_title,
            "--body",
            pr_body,
            "--head",
            branch_name,
            "--base",
            base,
        ],
        repo_path,
    )
    return pr_url
