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

🚧 Work in progress — built live during a hackathon.

## Project layout

- `agent/` — the agent itself (planning + tool loop)
- `demo-target-repo/` — a small seeded repo with intentional bugs, used for a reliable live demo
