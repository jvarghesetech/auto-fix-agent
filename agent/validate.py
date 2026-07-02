"""Independent test validation: don't trust the agent's self-report, actually run pytest."""

import subprocess
from dataclasses import dataclass


@dataclass
class TestResult:
    passed: bool
    output: str


def run_tests(repo_path: str) -> TestResult:
    """Run the repo's test suite via its own venv (falling back to system python)."""
    venv_python = f"{repo_path}/.venv/bin/python"
    python = venv_python if _exists(venv_python) else "python3"

    proc = subprocess.run(
        [python, "-m", "pytest", "-q"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = proc.stdout + proc.stderr
    return TestResult(passed=proc.returncode == 0, output=output)


def _exists(path: str) -> bool:
    import os

    return os.path.isfile(path)
