# auto-fix-agent

An autonomous coding agent that finds a bug in a target repo, writes a fix, validates it with tests, and opens a real pull request — no human in the loop.

Built with the [Claude Agent SDK](https://docs.claude.com/en/docs/agents-and-tools/claude-agent-sdk) for the agentic coding loop, plus `git`/`gh` for version control and PR creation.

## How it works

1. **Find** — the agent scans a target repo's open issues (or a seeded list of known bugs) and picks one to work on.
2. **Plan** — it reads the relevant code and drafts a fix plan.
3. **Fix** — it edits the code using file tools.
4. **Validate** — it runs the repo's test suite and iterates until tests pass.
5. **Ship** — it creates a branch, commits, pushes, and opens a PR via `gh`.

## Status

✅ Working end-to-end. Live proof: [PR #1](https://github.com/jvarghesetech/auto-fix-demo-target/pull/1),
opened autonomously against the seeded [demo target repo](https://github.com/jvarghesetech/auto-fix-demo-target).

## Project layout

- `agent/fixer.py` — runs the Claude Agent SDK loop that finds and fixes bugs
- `agent/validate.py` — independently re-runs the test suite (never trusts the agent's self-report)
- `agent/ship.py` — branches, commits, pushes, and opens the PR via `gh`
- `agent/run.py` — end-to-end CLI entrypoint tying it all together

## Usage

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python -m agent.run --repo https://github.com/<owner>/<repo>.git
```

The agent will clone the repo, diagnose and fix failing tests (retrying with real pytest
output fed back in if needed), independently verify the fix, then open a pull request.
