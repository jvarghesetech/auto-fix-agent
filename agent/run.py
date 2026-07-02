"""End-to-end CLI: clone a target repo, fix its failing tests, and open a PR.

Usage:
    python -m agent.run --repo https://github.com/<owner>/<repo>.git
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from agent.fixer import fix_until_passing
from agent.ship import open_pr


def _prepare_repo(repo_url: str, work_dir: Path) -> Path:
    subprocess.run(["git", "clone", repo_url, str(work_dir)], check=True)

    venv_dir = work_dir / ".venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    pip = venv_dir / "bin" / "pip"
    subprocess.run([str(pip), "install", "-q", "pytest"], check=True)

    requirements = work_dir / "requirements.txt"
    if requirements.exists():
        subprocess.run([str(pip), "install", "-q", "-r", str(requirements)], check=True)

    return work_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomously fix a repo's failing tests and open a PR.")
    parser.add_argument(
        "--repo",
        default="https://github.com/jvarghesetech/auto-fix-demo-target.git",
        help="Git URL of the target repo to fix.",
    )
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--keep", action="store_true", help="Keep the working directory after the run.")
    args = parser.parse_args()

    work_dir = Path(tempfile.mkdtemp(prefix="auto-fix-agent-"))
    print(f"[run] cloning {args.repo} into {work_dir}")

    try:
        _prepare_repo(args.repo, work_dir)

        print("[run] handing off to the agent...")
        passed = fix_until_passing(str(work_dir), max_attempts=args.max_attempts)

        if not passed:
            print("[run] agent could not get tests passing — not opening a PR.")
            sys.exit(1)

        branch_name = f"auto-fix/{int(time.time())}"
        pr_url = open_pr(
            repo_path=str(work_dir),
            branch_name=branch_name,
            commit_message="Fix failing tests via auto-fix-agent",
            pr_title="Fix failing tests (auto-fix-agent)",
            pr_body=(
                "This PR was opened autonomously by "
                "[auto-fix-agent](https://github.com/jvarghesetech/auto-fix-agent).\n\n"
                "The agent found failing tests, diagnosed the root cause in the source "
                "code, applied a fix, and independently verified the full test suite "
                "passes before opening this PR."
            ),
        )
        print(f"[run] PR opened: {pr_url}")

    finally:
        if args.keep:
            print(f"[run] work dir kept at {work_dir}")
        else:
            shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
